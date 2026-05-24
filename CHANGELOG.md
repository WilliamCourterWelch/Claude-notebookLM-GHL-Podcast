# Changelog

All notable changes to globalhighlevel.com's static-site build are documented here.

## [0.0.0.1] - 2026-05-23
### Fixed
- **Cross-language internal linking (GSC cliff fix).** English root `/category/` pages
  no longer list Spanish / India / Arabic posts. The May-7 fix only covered in-post
  links (`get_related`, `inject_internal_links`); `build_category_pages` still bucketed
  all 4 languages together. All listing builders (homepage, category pages, language
  hubs, language topic pages) now classify language consistently via `post_lang()`, so
  the 469 posts with no `language` field route correctly instead of defaulting to English.
  Verified by local build: 0 cross-language links across all 8 English category pages
  (was ~140+), 0 orphaned posts.
- **Language-bucket "categories" removed from the English root.** "GoHighLevel en Español"
  and "GoHighLevel India" no longer generate root `/category/` pages; their old URLs
  301-redirect to `/es/` and `/in/`.
- **Tightened language slug inference.** Dropped the `whatsapp` marker (a feature, not a
  geo signal — it misclassified genuine English posts as India); added `upi` / `razorpay`
  / `mena`.
