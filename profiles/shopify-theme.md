# Reviewing a Shopify theme

Read the store's release instructions and identify the intended theme before
running a command that can publish. This profile grants no publishing permission.

## Check the change

Compare local source with the current remote theme before making changes.
Merchants can edit theme settings in Shopify, so a clean Git checkout alone
does not show that local settings are current.

Run the repository's Liquid, JavaScript, and content checks. Verify prices,
ingredients, allergens, and other customer facts against their designated
source. Ask the owner when a fact is missing; do not infer it from old copy.

Use a Shopify preview for browser testing. Check the affected product page,
cart, or checkout handoff with realistic data. Local rendering cannot establish
that Shopify integrations work.

## If publishing is authorized

Follow the store's existing upload and activation process. Confirm the live
theme ID and uploaded file content afterward. A successful upload does not
necessarily activate the theme, and a partial upload may not remove deleted
files. Test a structural change through the store's supported release path.

Know how to restore the previous theme before activation. Check the asset URL
actually referenced by the page when cached CSS or JavaScript appears stale.
