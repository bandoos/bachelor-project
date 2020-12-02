# ptp base
FROM archlinux
RUN pacman --noconfirm -Syyu python python-pip \
	vim zip unzip \
	git gcc \
	figlet \
	sudo go \
	zsh

RUN useradd -m -s /bin/zsh production

# Create a temporary user to install trusted aur packages
# link yay related scripts
ADD .scripts/add-aur.sh /usr/sbin/add-aur
ADD .scripts/revoke-sudo.sh /usr/sbin/revoke-sudo
RUN chmod +x /usr/sbin/add-aur
RUN chmod +x /usr/sbin/revoke-sudo

RUN add-aur aur_user

# install aur packages
RUN su aur_user production -c \
	'yay -S --noprogressbar --needed --noconfirm mongodb-tools-bin bash-completion'

RUN revoke-sudo aur_user

ENV HOME /home/production
# Establish HOME
COPY . $HOME/
# copy source code
RUN chown -R production $HOME

RUN pip install argcomplete

# ** enter user configuration
USER production

ENV PATH="${HOME}/.local/bin:${PATH}"
ENV PYTHONPATH /home/production


WORKDIR $HOME
# Enter home folder
RUN sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

RUN mkdir data/
# setup data folder

RUN .scripts/install.sh
# install python dependencies

# set default env vars
# defaults to using local instance but can
# be customized at `docker run` time via -e <ENV>=<value>
# if the node needs to bootsrtap from non-local
# resources

# db for results filesystem
ENV EXECUTOR_GRIDFS='executor-gridfs'
# database uri
ENV MONGODB_URI='mongodb://0.0.0.0:27020'
# key value store / message broker
ENV REDIS_URI='redis://0.0.0.0:6399'

# ** link scripts
RUN chmod +x $HOME/.scripts/*
RUN ln $HOME/.scripts/* $HOME/.local/bin/

# ** Register autocopmetion hooks
RUN echo 'autoload -U bashcompinit && bashcompinit' >> .zshrc
RUN echo 'eval "$(register-python-argcomplete sim-stake)"' >> .zshrc
RUN echo 'eval "$(register-python-argcomplete sim-launcher)"' >> .zshrc
RUN echo 'eval "$(register-python-argcomplete dctl)"' >> .zshrc
RUN echo 'figlet -f slant pos-sim-core' >> .zshrc
RUN echo "echo '
Welcome to pos-sim-core docker environment.

If you see this message you have just started a new session.

Run

$ python -m sim.executor.config-doctor

to see if this instance is correctly configured and
ready to join the distributed system.

Use

$ run-worker

to have this machine run a worker node.

Use

$ launch-flower

to start monitoring the system from this machine.

Use the \"dctl\" program to fetch result files

(See project readme for complete instructions)

'"



CMD '/bin/zsh'
