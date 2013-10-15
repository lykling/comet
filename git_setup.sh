#!/bin/bash
if [[ $# -lt 1 ]]
then
	echo "Usage: ./git_setup <admin_public_key_path>";
	exit 1;
else
	adminkey=$1;
	git clone git://github.com/sitaramc/gitolite;
	mkdir -p $HOME/bin;
	gitolite/install -to $HOME/bin;
	bin/gitolite setup -pk $adminkey;
fi
exit 0;
