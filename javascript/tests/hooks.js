const sinon = require('sinon')

exports.mochaHooks = {
  afterEach () {
    sinon.restore()
  }
}
