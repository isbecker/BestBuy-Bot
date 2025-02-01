# RTX Best Buy Bot

## Features

- Refreshes link until "Add to Cart" button is available
- Automate entire checkout process

## Prerequisites

- Sign up for a Best Buy account
- Add all billing/shipping info to your account (must only have one card on the account)

## Dependencies

- [Nix](https://nixos.org/download.html)

  - [Nix Flake](https://nixos.wiki/wiki/Flakes)

- [Rye](https://rye.astral.sh/)

  - Comes with the flake if you use it

- [Just](https://github.com/casey/just)

  - Comes with the flake if you use it

- [Google Chrome](https://www.google.com/chrome/)

- [ChromeDriver](https://googlechromelabs.github.io/chrome-for-testing/)

## Running the Bot

1. Create a `config.yaml` file in the root directory of the project

1. Add the following to the `config.yaml` file:

   ```yaml
    email: "your_best_buy_email"
    password: "your_best_buy_password"
    cvv: "your_card_cvv"
    rtx_links:
    - https://www.bestbuy.com/site/card-name-goes-here/00000000.p?skuId=00000000
    - https://www.bestbuy.com/site/card-name-goes-here/00000000.p?skuId=00000000
    - https://www.bestbuy.com/site/card-name-goes-here/00000000.p?skuId=00000000
   ```

   The bot will go through the list one-by-one and check each of them to see if they
   are currently available to `Add to Cart`. If one of the links is available, the bot
   will proceed to checkout.

1. Run the bot with the following command:

   ```bash
   just run
   ```

> **💡 NOTE:** From testing, it appears that whether or not the CVV number is asked for depends on the price of the item. If you plan to use this bot for something cheaper, you may need to remove or comment out the segment of code that detects and fills in the CVV field. 🛠️
