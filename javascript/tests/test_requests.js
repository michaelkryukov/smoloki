const assert = require("assert");
const smoloki = require("../dist/smoloki.js");
const sinon = require("sinon");
const axios = require("axios");

describe("push", () => {
  let clock;

  before(() => {
    clock = sinon.useFakeTimers(1673798670922);
  });

  after(() => {
    clock.restore();
  });

  it("works", async () => {
    const post = sinon.replace(axios, "post", sinon.fake());

    await smoloki.push(
      { service: "web" },
      { level: "info", event: "visit", session: "icfhr9iyu34" },
      "host"
    );

    assert.ok(post.calledOnce);
    assert.equal(post.firstCall.args[0], "host/loki/api/v1/push");
    assert.deepEqual(post.firstCall.args[1], {
      streams: [
        {
          stream: {
            service: "web",
          },
          values: [
            [
              "1673798670922000000",
              "level=info event=visit session=icfhr9iyu34",
            ],
          ],
        },
      ],
    });
  });
});
