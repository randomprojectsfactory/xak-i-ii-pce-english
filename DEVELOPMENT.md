# Adapting Xak I & II to PC Engine CD

The goal was to retain the PCE game's presentation and Japanese performances while making its text and spoken scenes readable in English. The existing MSX translations provided a valuable starting point, but the PCE compilation required its own implementation.

## The MSX text was a reference, not a drop-in script

The supplied Xak I English reference came from the WOOMB translation, and Xak II from Oasis. Their disk layouts and text encodings differ from one another and from the PCE release. Some raw strings are inactive duplicates, fragments or older data; finding English bytes is not enough to establish which text the running game uses.

The PCE dialogue was extracted and indexed by its actual references. Corresponding MSX scenes were used for wording and terminology, then compared with the PCE Japanese text. Differences in names, scene structure, quantities, instructions and story details had to be resolved individually. Cinematic speech and other PCE-specific material also required separate caption text.

## Longer English text had to fit a banked engine

The HuC6280 addresses memory through 8 KB banks. Native scripts, pointers and control bytes depend on that arrangement. Simply replacing Japanese text with longer English sentences would overrun existing storage or cross a bank boundary incorrectly.

A dictionary-based compact text format and decoder were added in an available bank. The insertion process preserves the native script structure and control sequences, with checks that each packed string decodes back to its intended text. Separate font and text entry points manage the necessary bank changes and restore the caller's mapping afterward.

This distinction mattered in shops: a renderer could work in an ordinary conversation and fail when called from another UI bank. The shared font entry was made safe for those callers instead of fixing individual shop greetings.

## Readability required more than a Latin font

The initial compact font allowed English to fit, but a larger font was preferable on the PC Engine GT and on larger displays. The later layout keeps the original dialogue box and adds pages when the text reaches its usable area.

Pagination retains the original event until the final page is confirmed. Page advancement must not accidentally confirm the next event or a choice, and speaker changes, native waits and the final acknowledgement must retain their intended behavior. Lowercase letters with descenders also needed enough vertical space to avoid clipping on the bottom row.

The renderer draws through the game's tile system. Uploading more glyph data while blocking display interrupts could disturb the raster timing and make the picture move. The larger-font path was adjusted so the native display interrupts can continue during drawing and upload.

## A story-script inventory did not cover every interface

Shop descriptions, purchase questions, role headings, item labels and system messages use additional native consumers and repeated module copies. Several interactions therefore needed a separate audit beyond matching the story to the MSX references.

Native literal and table-based text consumers were inventoried independently. Their English replacements preserve prices, level requirements, page controls and pointer locations. The same changes were applied to the relevant copies throughout the compilation, rather than only to the first shop where a missing line was observed.

## The cinematics use the game's graphics pipeline

These scenes are not ordinary modern video files with an external subtitle track. Captions have to coexist with the game's own tile, palette, scrolling and scene-update behavior. CD-DA speech and ADPCM playback were audited separately to map the speech to the correct events and timings.

English captions are drawn by code running inside the game. Timing is tied to the relevant scene/playback sequence, with explicit cleanup at transitions and skip boundaries. Some longer passages require reading holds while retaining the original speech timing. Graphic text is replaced where appropriate or accompanied by a caption when retaining the original artwork better preserves its style.

Subtitle updates must also avoid overwriting graphics while they are still being displayed. The work included staging tile updates, coordinating palette and scroll changes, and adjusting display handoffs so a caption update does not briefly expose another portion of the image.

## Backup-memory access has its own display handoff

The save/load display issue involved the BIOS as well as the game. Backup-memory routines poll and acknowledge VBlank, so the game can miss its usual scroll initialization when execution returns. During that access, the BIOS scroll can also expose a normally hidden row of the background tilemap.

The correction aligns the entry handoff, temporarily saves and blanks that row during the BIOS call, then restores its exact contents and the normal scroll state on return. It preserves the BIOS result and the caller's bank and register state. The shared native UI paths cover boot loading, death loading and in-game backup menus without changing the save format.

## Disc layout and patch distribution

The source is a mixed-mode disc with 29 raw tracks. Only data Tracks 02 and 05 are changed; the remaining audio tracks stay byte-identical. The track sizes and layout are retained, and modified Mode 1 sectors have regenerated error-detection and correction data.

The public patches are made directly from the unmodified Japanese source to the published English image. They do not require an intermediate build. Applying each patch was checked against the complete target-track hash. The public package contains only the differences, a source-hash manifest, a patching utility and documentation; it contains no disc image or audio track.
