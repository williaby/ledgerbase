decrypt_env.sh
==============

**Description**: Decrypts the LedgerBase environment files using sops.

**Category**: dev

**Usage**:

.. code-block:: bash

   ./decrypt_env.sh

**Behavior**:
Decrypts .env.enc and .env.prod.sops.yaml into plaintext .env files for local use.

**Inputs**:
- .env.enc
- .env.prod.sops.yaml

**Outputs**:
- .env
- ledgerbase_secure_env/.env.prod

**Dependencies**:
- sops
- bash

**Tags**: secrets, env, sops, decryption

**Author**: Byron Williams

**Last Modified**: 2025-04-12
