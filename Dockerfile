# ptp base
FROM archlinux
RUN pacman --noconfirm -Syyu python python-pip \
	vim zip unzip \
	git gcc \
	figlet \
	sudo go

RUN useradd -m -s /bin/bash production

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

RUN mkdir data/
# setup data folder

RUN .scripts/install.sh
# install python dependencies

# set default env vars
# defaults to using local instance but can
# be customized at `docker run` time via -e <ENV>=<value>
# if the node needs to bootsrtap from non-local
# resources

ENV EXECUTOR_GRIDFS='executor-gridfs'
# db for results filesystem

ENV MONGODB_URI='mongodb://localhost:27020'
# database uri

ENV REDIS_URI='redis://localhost:6399'
# key value store / message broker

# ** link scripts
RUN chmod +x $HOME/.scripts/*
RUN ln $HOME/.scripts/* $HOME/.local/bin/

# RUN ln $HOME/.scripts/get-batch-file.sh $HOME/.local/bin/get-batch-file
# RUN ln $HOME/.scripts/list-batch-files.sh $HOME/.local/bin/list-batch-files


# ** Register autocopmetion hooks
RUN echo 'eval "$(register-python-argcomplete sim-stake)"' >> .bashrc
RUN echo 'eval "$(register-python-argcomplete sim-launcher)"' >> .bashrc

CMD '/bin/bash'
