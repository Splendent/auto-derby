const { execSync, exec } = require("child_process");
const { relative, dirname } = require("path");

const workspaceFolder = dirname(__dirname);

/**
 *
 * @param {string} command
 * @returns {string}
 */
function shell(command) {
  return execSync(command).toString().trimEnd();
}

/**
 *
 * @param {string} text
 * @return {string}
 */
function quotePython(text) {
  return text.replace(/\\/, "\\\\").replace(/'/g, `\\'`);
}

/**
 * @type {{
 *    readVersion: (content: string) => string,
 *    writeVersion: (content: string, version: string) => string,
 * }}
 * @link https://github.com/conventional-changelog/standard-version#custom-updaters
 */
module.exports = {
  readVersion(content) {
    return (/VERSION = '(.+)'/.exec(content) || [undefined])[1];
  },
  writeVersion(content, version) {
    return `\
# -*- coding=UTF-8 -*-
# Code generated by ${relative(workspaceFolder, __filename)}, DO NOT EDIT
# fmt: off
"""
version info.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import datetime

VERSION = "${version}"
RELEASE_DATE = datetime.fromtimestamp(${(Date.now() / 1e3).toFixed()})
LAST_GIT_COMMIT_DESCRIBE = "${shell("git describe --always --match v*.*.*")}"
LAST_GIT_COMMIT_HASH = "${shell("git log -1 --pretty=%H")}"
LAST_GIT_COMMIT_AUTHOR_NAME = "${quotePython(
      shell('git log -1 "--pretty=%an"')
    )}"
LAST_GIT_COMMIT_AUTHOR_EMAIL = "${quotePython(
      shell('git log -1 "--pretty=%ae"')
    )}"
LAST_GIT_COMMIT_AUTHOR_DATE = datetime.fromtimestamp(${shell(
      'git log -1 "--pretty=%at"'
    )})
LAST_GIT_COMMIT_SUBJECT = "${quotePython(shell('git log -1 "--pretty=%s'))}"
LAST_GIT_COMMIT_BODY = "${quotePython(shell('git log -1 "--pretty=%b'))}"
`;
  },
};
