## How was `SLACK_API_TOKEN` created

1. Go to https://api.slack.com/apps

2. Click Create an App > select From scratch
    - App Name = **Ursabot**
    - Workspace = (select workspace)
    - click Create App

3. Click Edit Manifest on On App Summary
    - Paste yaml below into YAML field
    - click Save Changes

    ```yaml
    _metadata:
      major_version: 1
      minor_version: 1
    display_information:
      name: "**Ursabot**"
    features:
      bot_user:
        display_name: ursabot
    oauth_config:
      scopes:
        bot:
          - chat:write
    settings:
      org_deploy_enabled: false
      socket_mode_enabled: false
      token_rotation_enabled: false
    ```

4.  Click OAuth & Permissions
    - click Install to Workspace
    - click Allow
    - copy Bot User OAuth Token and use it for `SLACK_API_TOKEN`
 
5.  Go to Slack > Channel where you want Ursabot to be able to post message
    - Post this message: "/invite @ursabot"
