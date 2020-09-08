# Ansible Tower / AWX plugin for Cloudify

## Packaging

To build the plugin *wagon* file, use the Cloudify Wagon Builder container image. 

```
docker run \
  -v /path/to/cloudify-ansible-tower-plugin/:/packaging \
  --name cfy-builder \
  cloudifyplatform/cloudify-centos-7-wagon-builder
```