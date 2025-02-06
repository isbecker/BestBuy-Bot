# RTX Best Buy Bot 🚀

## Features ✨

- 🔄 Refreshes link until "Add to Cart" button is available
- 🤖 Automate entire checkout process
- ⚖️ Prioritizes items based on weights in the config

## Prerequisites 📋

- 📝 Sign up for a Best Buy account
- 💳 Add all billing/shipping info to your account (must only have one card on the account)
- 🛒 Add all the items you want to the saved items in the account before starting the bot

## Dependencies 📦

- [Nix](https://nixos.org/download.html)
  - [Nix Flake](https://nixos.wiki/wiki/Flakes)
- [Rye](https://rye.astral.sh/)
  - Comes with the flake if you use it
- [Just](https://github.com/casey/just)
  - Comes with the flake if you use it
- [Google Chrome](https://www.google.com/chrome/)
- [ChromeDriver](https://googlechromelabs.github.io/chrome-for-testing/)

## Configuration ⚙️

You can configure the bot using environment variables or a configuration file. The following environment variables are used:

- `BOT_EMAIL`: Your Best Buy account email
- `BOT_PASSWORD`: Your Best Buy account password
- `BOT_CVV`: Your card CVV
- `CHROMIUM_VERSION`: The version of Chromium to use (optional)
- `LOG_LEVEL`: The log level for the bot (optional, defaults to INFO)

### Using Environment Variables 🌐

Create a `.env` or `.env.local` file in the root directory of the project with the following content:

```env
BOT_EMAIL=your_best_buy_email
BOT_PASSWORD=your_best_buy_password
BOT_CVV=your_card_cvv
CHROMIUM_VERSION=desired_chromium_version
LOG_LEVEL=INFO
```

### Using Environment Variables in `config.yaml` with OmegaConf 🛠️

This project uses [OmegaConf](https://omegaconf.readthedocs.io/) for configuration management. The default `config.yaml` file uses this feature to reference environment variables. You can see an example in the next section.

## Running the Bot

1. Create a `config.yaml` file in the root directory of the project

1. Add the following to the `config.yaml` file:

   ```yaml
    email: "${oc.env:BOT_EMAIL}"
    password: "${oc.env:BOT_PASSWORD}"
    cvv: "${oc.env:BOT_CVV}"
    chromium:
      version: 132  # Add your desired Chromium version here, optional
    links:
      - url: https://www.bestbuy.com/site/card-name-goes-here/00000000.p?skuId=00000000
        weight: 10
      - url: https://www.bestbuy.com/site/card-name-goes-here/00000000.p?skuId=00000000
        weight: 5
      - url: https://www.bestbuy.com/site/card-name-goes-here/00000000.p?skuId=00000000
        weight: 1
   ```

   The bot will go through the list one-by-one and check each of them to see if they
   are currently available to `Add to Cart`. If one of the links is available, the bot
   will proceed to checkout. The bot will prioritize items based on the weights specified in the config.

1. Run the bot with the following command:

   ```bash
   just run
   ```

## New Algorithm with Saved Items Page

The bot now uses a new algorithm that interacts with the saved items page on your Best Buy account. This algorithm will:

1. Log in to your Best Buy account.
1. Navigate to the saved items page.
1. Check the availability of each item in your saved items list.
1. Prioritize items based on the weights specified in the `config.yaml` file.
1. Attempt to add the highest priority available item to the cart.
1. Proceed to checkout if an item is successfully added to the cart.

This approach ensures that the bot focuses on the items you have saved and prioritizes them according to your preferences.

> **💡 NOTE:** From testing, it appears that whether or not the CVV number is asked for depends on the price of the item. If you plan to use this bot for something cheaper, you may need to remove or comment out the segment of code that detects and fills in the CVV field. 🛠️

## Contributing 🤝

We welcome contributions! Please fork the repository and submit a pull request for any changes you'd like to make.

## License 📄

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
