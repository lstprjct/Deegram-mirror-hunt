## Deploying Mirrorbot on Heroku with Github Workflows.

## Pre-requisites

- [token.pickle](https://github.com/Anime-Republic/Mirror-New/blob/main/CreateSA.md#getting-google-oauth-api-credential-file)
- [Heroku  accounts](https://id.heroku.com)
- Recommended to use 1 App in 1 Heroku account
- Note: Don't use bin/fake credits card, because your Heroku account will get banned.

## Deployment

1. Fork or Import this repo and Fill up `config.env` & `drive_folder`
2. Then upload **token.pickle** to your forks, or you can upload your **token.pickle** to your Index and put your **token.pickle** link to `TOKEN_PICKLE_URL` (**NOTE**: If you don't upload **token.pickle** uploading will not work).
3. Upload account folder if USE_SERVICE_ACCOUNT is True Else Fill up `ACCOUNTS_ZIP_URL`
4. Go to Repository `Settings` -> `Secrets`

	![secrets](https://telegra.ph/file/f9fa2c5e5aa9f49868a23.jpg)
  
5.Add the below Required Variables one by one by clicking `New Repository Secret` everytime.

	* `HEROKU_EMAIL` Heroku Account Email Id in which the above app will be deployed
	* `HEROKU_API_KEY` Your Heroku API key, get it from https://dashboard.heroku.com/account
	* `HEROKU_APP_NAME` Your Heroku app name, Name Must be unique
6. After adding all the above Required Variables go to Github Actions tab in your repo.
7. Select `Manually Deploy to Heroku` workflow as shown below:

  ![Example Manually Deploy to Heroku](https://telegra.ph/file/61f6fb3400e3410ccd647.png)
  
8.Then click on Run workflow

9.**Done!** your bot will be deployed now.	


## NOTE
- Don't change/edit variables from Heroku if you want to change/edit do it from `config.env`
