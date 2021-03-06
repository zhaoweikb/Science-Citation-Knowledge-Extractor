/**
* Copyright 2012-2016, Plotly, Inc.
* All rights reserved.
*
* This source code is licensed under the MIT license found in the
* LICENSE file in the root directory of this source tree.
*/

'use strict';

var Registry = require('../registry');
var Lib = require('../lib');


module.exports = function register(_modules) {
    if(!_modules) {
        throw new Error('No argument passed to Plotly.register.');
    }
    else if(_modules && !Array.isArray(_modules)) {
        _modules = [_modules];
    }

    for(var i = 0; i < _modules.length; i++) {
        var newModule = _modules[i];

        if(!newModule) {
            throw new Error('Invalid module was attempted to be registered!');
        }

        switch(newModule.moduleType) {
            case 'trace':
                registerTraceModule(newModule);
                break;

            case 'transform':
                registerTransformModule(newModule);
                break;

            case 'component':
                registerComponentModule(newModule);
                break;

            default:
                throw new Error('Invalid module was attempted to be registered!');
        }
    }
};

function registerTraceModule(newModule) {
    Registry.register(newModule, newModule.name, newModule.categories, newModule.meta);

    if(!Registry.subplotsRegistry[newModule.basePlotModule.name]) {
        Registry.registerSubplot(newModule.basePlotModule);
    }
}

function registerTransformModule(newModule) {
    if(typeof newModule.name !== 'string') {
        throw new Error('Transform module *name* must be a string.');
    }

    var prefix = 'Transform module ' + newModule.name;

    if(typeof newModule.transform !== 'function') {
        throw new Error(prefix + ' is missing a *transform* function.');
    }
    if(!Lib.isPlainObject(newModule.attributes)) {
        Lib.log(prefix + ' registered without an *attributes* object.');
    }
    if(typeof newModule.supplyDefaults !== 'function') {
        Lib.log(prefix + ' registered without a *supplyDefaults* function.');
    }

    Registry.transformsRegistry[newModule.name] = newModule;
}

function registerComponentModule(newModule) {
    Registry.componentsRegistry[newModule.name] = newModule;
}
