# Ansible Tower / AWX plugin for Cloudify

## Packaging

To build the plugin *wagon* file, use the Cloudify Wagon Builder container image. 

```
docker run \
  -v /path/to/cloudify-ansible-tower-plugin/:/packaging \
  --name cfy-builder \
  cloudifyplatform/cloudify-centos-7-wagon-builder
```

## Importing

In Cloudify, go to the *System Resources* menu and click the *Upload* button within the *Plugins* widget. Use the Wagon file (.wgn) from the last section and the plugin.yaml file from this repo. 

![Importing a Cloudify plugin](static/screenshots/cfy1.png)

![Listing Cloudify plugins](static/screenshots/cfy2.png)

## AWX / Ansible Tower authentication

Cloudify needs to perform actions as a user within AWX / Ansible Tower. To do this, it needs a *Personal Access Token (PAT)*. Within AWX/Tower, go to the *Users* menu, click on the user you want to authenticate as, click the *TOKENS* top menu button, and click the *+ (plus symbol)*. 

Unless you have a specific use case, leave the *APPLICATION* field blank and change the *SCOPE* field to *Write*. The token issued should be used within your Cloudify blueprint. 

![Creating an Ansible Tower token](static/screenshots/awx1.png)

![Displaying an Ansible Tower token](static/screenshots/awx2.png)

![Listing Ansible Tower tokens](static/screenshots/awx3.png)

