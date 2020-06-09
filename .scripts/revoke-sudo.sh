set -o pipefail -e

if test -z "$1"
then
   echo "You must specify a user name"
   exit -1
fi

AUR_USER=$1
sed -i "s/$AUR_USER      ALL = NOPASSWD: ALL//" /etc/sudoers
