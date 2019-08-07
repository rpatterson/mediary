=========================================
mediary
=========================================
Media processing and management utilities
-----------------------------------------

This is a collection of tools and utilities for processing media files and
managing media libraries.  It strives to follow the Unix philosophy of
DOTADIW, "Do One Thing And Do It Well."  The goal is to break the necessary
work down into tasks that are as discrete as possible so that they can be
composed variously to serve different environments and workloads.  Examples of
different ways to compose these tools may be provided but are not the only way
to do it.  Just some of the many benefits of this approach are:

- easier to execute steps in parallel for faster execution
- easier to execute individual steps when they fail in special cases

Until there's a clear reason not to, workflows will be supported by composing
these utilities in process pipelines using ``|``.  The ``stdin`` for each
utility should accept one media file per line/NULL, and each utility should output
the next relevant media file one per line/NULL.

When managing a media library, there are different phases that media progress
through leading to full integration into the library:

Acquisition:
    new media to be integrated into the library

Processing:
    processing newly acquired media into an acceptable form for integrating
    the into library

Integration:
    adding processed media into the library to make it available to consumers


Processing
==========

Newly acquired media may have a number of issues making it unacceptable for
integrating into the library.  It may be in a format unsupported by the
library software.  It may be in a format that is in some way sub-optimal.  It
may be poorly named leading to mis-identification my the library software.
Etc..

The processing tools here support the following workflow, but may be composed
differently to accommodate different workflows:

#. Extract Archives

   Extract media from compressed archives (e.g. ``*.rar``, ``*.zip``,
   ``*.tar.gz``) as needed.  Media formats are already highly compressed so
   such formats have no benefit and cause many issues with library and player
   software.  This is well covered by existing utilities, so this goal is
   accomplished by integrating those utilities into the pipeline/workflow.

#. Convert

   Convert newly acquired media to optimal formats including:

   - remux into the optimal container format
   - transcode streams to optimal codecs, both video and audio

   Since conversion may require lots of computational power, optimization is
   important here.  These are done in one step/tool in an exception to DOTADIW
   because it's much more efficient to do in one step, e.g. because ``ffmpeg``
   can do them at once.

   Similarly, the utility for this step strives to optimize the processing as
   much as possible, e.g. using ``ffmpeg`` hardware acceleration based on what
   hardware is available.  For many media libraries, completeness is more
   important that optimization, so if an optimized conversion fails, the
   conversion will be attempted again without optimization.

#. Tag

   Embed metadata into tags per the format.

#. Optimize

   Perform other optimizations, e.g. placement of the MOOV atom for
   quickstart.
