# Cofr, safely backup sensitive data using your Trezor wallet

Cofr is a standalone tool that helps you encrypt and backup sensitive text
data, using the Trezor hardware wallet.

With Cofr, you can safely store passwords, private keys or
cryptocurrency wallet seeds and backup them on Dropbox, Google Drive or any
other cloud service.

It runs in a shell. Here's an usage sample:

    $ cofr -f ~/Dropbox/important_and_secret_data.db
    Please, confirm store decryption on the device.

    Welcome to the Cofr shell. Type help or ? for command list.

    This software comes with NO WARRANTY whatsoever. Use it at your own risk.
    Make sure to **backup** your store file.

    Cofr> list
    Here is the list of all known items:
     - $monero wallet seed
     - $iota wallet seed
     - bahamas bank account password
     - favorite hitman phone number
     - secret french pancake recipe
     Cofr> get secret french pancake recipe
    Please, confirm key decryption on the device.
    <censored… for national security reasons>
    Cofr> put $nano wallet seed
    Please, provide the value for key "$nano wallet seed": e217e2727ba080bf9fbab9c93bd8ba71eeecef3cac1dcb64c0ce4d7908712561
    Done!
    Cofr> sync
    Changes written back to disk.
    Cofr> quit
    Bye!


## Warning

This code is **not** officially supported by SatoshiLabs (the company behind
Trezor).

This software is provided "as is" and comes with absolutely no warantee of any
kind. Use it at your own risk. See the [complete license](LICENSE.md).


## What is it?

Cofr lets you read and write small chunks of text data in a file. Cofr uses
strong encryption, so you can backup the resulting file in cloud storage, even
from a provider you don't trust.

Internally, Cofr connects to your Trezor to generate *deterministic encryption
keys*. It means that the key used to encrypt the Cofr file *derives from your
Trezor seed*.

You don't have to remember yet another password to encrypt / decrypt Cofr
files, all you need is one click on the hardware wallet. Still, if your Trezor
is lost or damaged, as long as you have a backup of your seed, you will be able
to retrieve the content of your Cofr file.

Cofr is a command-line tool that runs in a shell and provides it's own set of
commands. It's written in Python and is published under a permissive
open-source license.


## Requirements

For Cofr to work, you need the following elements:

 - a working computer with an up-to-date python (>=3.5) installation ;
 - a working and plugged-in Trezor hardware wallet ;
 - access to a shell ;
 - that's about it.


## Usage

Let's say you have a very private piece of information that you want to protect
at all costs. For example, you bought some [$NANO](https://nano.org), a
cryptocurrency that is not supported by Trezor at the moment, and you want to
backup your wallet seed.

### Storing data

Make sure your Trezor is plugged, then type in a shell:

    cofr -f ~/Dropbox/crypto.db

If the file `~/Dropbox/crypto.db` does not already exist, you will be prompted
for confirmation and it will be created. You also need to physically activate
the file encryption on the Trezor.

Once this is done, you get access to the Cofr shell.

    Cofr>

Type in some commands to read existing data, or add new data in the store.

Here is the list of available commands:

 * `list`: List all items in the file.
 * `put`: Store a new item in the file.
 * `get`: Display a specific item's content.
 * `del`: Remove an item from the file.
 * `sync`: Write changes back to disk.
 * `quit`: Exit the shell.

To store new data in the Cofr file, use the `put` command followed by the item
identifier:

    Cofr> put nano_wallet_seed
    Please, provide the value for key "nano_wallet_seed": e217e2727ba080bf9fbab9c93bd8ba71eeecef3cac1dcb64c0ce4d7908712561
    Done!

**Please note that nothing will happen until you actually commit the changes
to the Cofr file using the `sync` command.**

    Cofr> sync
    Changes written back to disk.

You can then safely exit Cofr:

    Cofr> quit
    Bye!

### Retrieving data

Let's say you want to impress some friends and need access to the secret french
pancake recipe that is passed on within your family since centuries. Time for
data retrieval !

Start Cofr like you did before. Once again, you will have to manually confirm
the file decryption on the Trezor.

Then, use the `list` command to see existing items in the Cofr file, or
retrieve the value associated with an item using the `get` command. As soon as
you confirm the item decryption on the Trezor, it's content will appear.

    Cofr> get secret french pancake recipe
    Please, confirm key decryption on the device.
    You need:
      - five eggs
      - butter
      - free and immediate access to a willing cow
      <censored>


### Backuping your Cofr file

Cofr does not backup your data for you. You are responsible for backuping your
Cofr file. If your data is *really* sensitive, store it in several cloud
services, make copy on thumb drives and give them to your relatives.

Don't worry, your data is safe, and nobody can access it without your Trezor or
it's seed.


## Installation

Note that you need Python >= 3.5 to run Cofr.

### With Pipsi (recommended)

If you don't use [Pipsi](https://github.com/mitsuhiko/pipsi), you're missing
out.

    pipsi install cofr

### With Pip

Make sure to manually create a virtualenv before. Then:

    pip install --user cofr

### From source

You will need [Pipenv](https://docs.pipenv.org/).

    git clone https://github.com/thibault/cofr.git
    cd cofr
    pipenv install
    pipenv run cofr


## Data safety, encryption, technical information

You can read this part if you want to know more about Cofr's internals.

Cofr uses a double level of encryption to make sure your data is safe. First,
each item is individually encrypted *then* the complete file is encrypted
before being stored on disk. It means that even if an attacker could somehow
get a hand on a decrypted Cofr file content, they still would need to break
each and every one item encryption to access it.

The mechanisms used by Cofr are very similar to those used in SatoshiLab's
password manager, and [described in this
document](https://github.com/satoshilabs/slips/blob/master/slip-0016.md).

In short, Cofr connects to the Trezor using the official SatoshiLab's api to
generate *deterministic encryption keys*, and then uses those keys to encrypt
your data with AES-GCM.

What this means is that the actual content encryption takes place on your
computer, using a standard encryption algorithm (AES). AES is a symmetric
algorithm, meaning the same key is used for encryption and decryption.

Cofr uses the SatoshiLab's official Trezor API to generate encryption key that
are *deterministic*, i.e they derives from your private key, but cannot be
reproduced without your Trezor or it's seed.

The reason it works this way is because it would be inefficient to directly
encrypt large chunks of text on the Trezor itself, and it could take a
noticeably long amount of time. Instead, the encryption runs on your own cpu
and uses standard battle-tested encryption algos, while the Trezor gives you
the guarantee that your data cannot be decrypted without your private key.


## Safety considerations

**PLEASE READ THIS OR YOUR FUNDS WILL GET STOLEN.** We will not be held
responsible if anything bad happens to you because your usage of this tool.


### Ways you could lose your data

For information purpose, here is a (non comprehensive) list of events that
might lead you to **completely** and **irreversibly** lose access to your
secret data:

 * The Cofr data file is erased by mistake and you don't have any backup.
 * The Cofr data file is corrupted because of a faulty hard drive, and you
   don't have any backup.
 * You computer burns, and you don't have any backup.
 * Your hard drive is stolen by an extraterrestrial invasion force scout, and
   you don't have any backup (do you start to notice a pattern here?).
 * Your Trezor is lost / stolen / damaged and you don't have a backup of the
   Trezor seed. Without the private key stored in the hardware wallet, the Cofr
   file decryption *will be impossible*.

To mitigate those issues:

 * Make **several backups** of the cofr data files, e.g in Dropbox or subscribe
   to a cloud-based backup service.
 * Take every measure to make sure your Trezor seed is safe.


### Ways your data could be leaked

Here is a list of events that might lead to a leak of your secret data, causing
an eventual theft of your funds:

 * Your secret data was generated and / or handled *before encryption* on an
   unsafe computer hosting a malware / spyware / keylogger / etc.
 * Your Trezor seed is leaked.
 * Some malicious hacker hijacked my computer and uploaded a modified version
   of Cofr designed to discretely upload data to a remote server.
 * I'm a malicious hacker trying to scam you.

To mitigate those issues:

 * Only manipulate sensitive data on safe, trusted and up-to-date computers,
   e.g computers unplugged from the internet and booted on a [live linux
   system](https://tails.boum.org/).
 * Trust no one, and inspect the source code yourself. Ask people you trust to
   do the same.

Cofr uses mathematically proven encryption methods, but if you use a tool to
handle highly sensitive data on an unsafe computer, the amount of protection
you receive is None.


## Issues and improvements

If you want to report an issue or suggest an improvement, you can do
so by [submitting a Github issue](https://github.com/thibault/cofr/issues).


## Where does the name comes from?

In french, *un coffre* is a safe. Hence, Cofr. Do you know how hard it is to
find good and available project names?


## Credits

Crafted with love by [Thibault Jouannic](https://www.miximum.fr/). I'm a french
freelance developer, [sometimes available for
hire](https://www.miximum.fr/pages/prestations/).

You can contact me by email or via [twitter at
@thibaultj](https://twitter.com/thibaultj).
