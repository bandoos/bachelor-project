import os
from  sim.executor.logger import logger
from pprint import pprint
import redis
from sim.executor.dbdriver import Client
from pymongo.errors import ConnectionFailure

if __name__ == "__main__":

    print("""

    sim-core-0.1.0 configuration doctor

    ------------------------

This script will verify wheter the environment variables,
    within the rerminal session it is run in,
    are valid.

    You can either 'export' variables manually

    $ export MY_VARIABLE=my-value

    or source an env file

    $ source .scripts/source-env.sh <env-file>

    from the PROJECT_ROOT

    """)
    env=os.environ

    summary = {}
    logger.info("==> Starting config doctor <==")

    logger.info("--> Cheking redis configuration ...")


    if env.get('REDIS_URI') and env.get('REDIS_DB'):
        logger.info("REDIS_URI and REDIS_DB variables exist.")
        broker_url=env.get('REDIS_URI') + '/' + env.get('REDIS_DB')

        logger.info("REDIS_URI/REDIS_DB is: {}".format(broker_url))
        summary['redis'] = {'vars_feedback': 'ok',
                            'REDIS_URI':     env['REDIS_URI'],
                            'REDIS_DB':      env['REDIS_DB']}

        logger.info('Verifying that redis is reachable...')
        ping=None
        try:
            r = redis.from_url(broker_url)
            res = r.ping()
            logger.info(f"REDIS PING: {res}")
            ping='ok'
        except ValueError as e:
            logger.error('The value for REDIS_URI or REDIS_DB is invalid:',exc_info=e)
            ping=e
        except redis.exceptions.ConnectionError as e:
            logger.error(f'Cannot ping {broker_url}',exc_info=e)
            ping=e
        except Exception as e:
            logger.error('An error occured while trying to ping redis',exc_info=e)
            ping=e
        summary['redis']['ping'] = ping

    else:
        logger.error("Redis variables are not properly configured:\n"+
                    "REDIS_URI="+str(env.get('REDIS_URI'))+ "\n"+
                    "REDIS_DB="+str(env.get('REDIS_DB')))
        logger.warning("Maybe you forgot to source the env file via .scripts/source-env.sh?")

        summary['redis'] = {'vars_feedback': 'ERROR: missing vars'}


    logger.info("--> Cheking mongodb configuration ...")

    if env.get('MONGODB_URI') and env.get('EXECUTOR_DB') and env.get('EXECUTOR_GRIDFS'):
        logger.info("MONGODB_URI and EXECUTOR_DB variables exist.")
        result_backend=env.get('MONGODB_URI') + '/' + env.get('EXECUTOR_DB')

        logger.info("MONGODB_URI/EXECUTOR_DB is: {}".format(result_backend))
        logger.info("EXECUTOR_GRIDFS is {}".format(env['EXECUTOR_GRIDFS']))

        summary['mongodb'] = {'vars_feedback':    'ok',
                              'MONGODB_URI':      env['MONGODB_URI'],
                              'EXECUTOR_DB':      env['EXECUTOR_DB'],
                              'EXECUTOR_GRIDFS':  env['EXECUTOR_GRIDFS']}
        logger.info("Verifying that mongodb is reachable...")

        ping=None
        try:
            c = Client(result_backend=result_backend)
            c.admin.command('ismaster')
            logger.info("MONGODB PING: True")
            ping='ok'
        except ValueError as e:
            logger.error('The value for MONGODB_URI or EXECUTOR_DB is invalid',exc_info=e)
            logger.warning('If you forgot the schema prefix "mongodb://" the error above will '+
                           'not be very informative! Check that before panicking!')
            ping=e
        except ConnectionFailure as e:
            logger.error(f'Cannot ping {result_backend}',exc_info=e)
            ping=e
        except Exception as e:
            logger.error("An error occurred while trying to ping mongodb",exc_info=e)
            ping=e
        summary['mongodb']['ping'] = ping


    else:
        logger.error("Mongodb variables are not properly configured:\n"+
                     "MONGODB_URI="+str(env.get('MONGODB_URI'))+ "\n"+
                     "EXECUTOR_DB="+str(env.get('EXECUTOR_DB'))+ "\n"+
                     "EXECUTOR_GRIDFS="+str(env.get('EXECUTOR_GRIDFS')))

        logger.warning("Maybe you forgot to source the env file via .scripts/source-env.sh?")

        summary['mongodb'] = {'vars_feedback': 'ERROR: missing vars'}

    logger.info("--> Cheking worker configuration ...")

    if env.get('INIT_WORKERS_N') and env.get('TZ'):
        logger.info("INIT_WORKERS_N and TZ variables exist")
        logger.info(f"INIT_WORKERS_N={env['INIT_WORKERS_N']}")
        logger.info(f"TZ={env['TZ']}")
        summary['worker'] = {'vars_feedback' : 'ok',
                             'INIT_WORKERS_N' : env['INIT_WORKERS_N'],
                             'TZ':            env['TZ']}

    else:
        logger.error('Worker variables are not properly configured:\n'+
                     f'INIT_WORKERS_N={env.get("INIT_WORKERS_N")}\n'+
                     f'TZ={env.get("TZ")}')
        summary['worker'] = {'vars_feeback': 'ERROR: missing vars'}

    logger.info("Providing overall summary:")
    pprint(summary)
