const {
  logfmtDump,
  logfmtLoad,
  _logfmtUnescape,
} = require("../dist/smoloki.js");
const assert = require("assert");

const CASES = [
  [{ key: "value" }, "key=value"],
  [{ key: '"value"' }, 'key="\\"value\\""'],
  [{ key: "v=alue" }, 'key="v=alue"'],
  [{ key: "va l ue" }, 'key="va l ue"'],
  [{ key: "va\\l\\ue" }, "key=va\\\\l\\\\ue"],
  [{ key: "va\nl\nue" }, "key=va\\nl\\nue"],
  [{ key: "'" }, "key='"],
  [{ key: '"' }, 'key="\\""'],
];

describe("logfmtDump", () => {
  describe("dumps", () => {
    for (const [originalValue, dumpedValue] of CASES) {
      it(`${JSON.stringify(originalValue)}`, () => {
        assert.equal(logfmtDump(originalValue), dumpedValue);
      });
    }

    it('{"key":1}', () => {
      assert.equal(logfmtDump({ key: 1 }), "key=1");
    });

    it('{"key":1.5}', () => {
      assert.equal(logfmtDump({ key: 1.5 }), "key=1.5");
    });
  });

  describe("loads", () => {
    for (const [originalValue, dumpedValue] of CASES) {
      it(`${dumpedValue}`, () => {
        assert.deepEqual(logfmtLoad(dumpedValue), originalValue);
      });
    }
  });

  describe("_logfmtUnescape", () => {
    it('"hey"', () => {
      assert.equal(_logfmtUnescape('"hey"'), "hey");
    });

    it('"\\"hey\\""', () => {
      assert.equal(_logfmtUnescape('"\\"hey\\""'), '"hey"');
    });
  });
});
