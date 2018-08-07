define([
  'sources/gettext', 'alertify', 'jquery',
], function(gettext, alertify, $) {
  alertify.defaults.transition = 'zoom';
  alertify.defaults.theme.ok = 'btn btn-primary';
  alertify.defaults.theme.cancel = 'btn btn-danger';
  alertify.defaults.theme.input = 'form-control';
  alertify.defaults.closable = false;
  alertify.pgIframeDialog || alertify.dialog('pgIframeDialog', function() {
    var iframe;
    return {
      // dialog constructor function, this will be called when the user calls
      // alertify.pgIframeDialog(message)
      main: function(message) {
        //set the videoId setting and return current instance for chaining.
        return this.set({
          'pg_msg': message,
        });
      },
      // we only want to override two options (padding and overflow).
      setup: function() {
        return {
          options: {
            // Disable both padding and overflow control.
            padding: !1,
            overflow: !1,
            closable: true,
          },
        };
      },
      // This will be called once the DOM is ready and will never be invoked
      // again. Here we create the iframe to embed the video.
      build: function() {
        // create the iframe element
        iframe = document.createElement('iframe');

        iframe.src = '';
        iframe.frameBorder = 'no';
        iframe.width = '100%';
        iframe.height = '100%';

        // add it to the dialog
        this.elements.content.appendChild(iframe);

        //give the dialog initial height (half the screen height).
        this.elements.body.style.minHeight = screen.height * .5 + 'px';
      },
      // dialog custom settings
      settings: {
        pg_msg: undefined,
      },
      // listen and respond to changes in dialog settings.
      settingUpdated: function(key, oldValue, newValue) {
        switch (key) {
        case 'pg_msg':
          var doc = iframe.contentWindow || iframe.contentDocument;
          if (doc.document) {
            doc = doc.document;
          }

          doc.open();
          doc.write(newValue);
          doc.close();

          break;
        }
      },
      // listen to internal dialog events.
      hooks: {
        // triggered when a dialog option gets update.
        // warning! this will not be triggered for settings updates.
        onupdate: function(option, oldValue, newValue) {
          switch (option) {
          case 'resizable':
            if (newValue) {
              this.elements.content.removeAttribute('style');
              iframe && iframe.removeAttribute('style');
            } else {
              this.elements.content.style.minHeight = 'inherit';
              iframe && (iframe.style.minHeight = 'inherit');
            }
            break;
          }
        },
      },
    };
  });
  alertify.pgNotifier = function(type, xhr, promptmsg, onJSONResult) {
    var msg = xhr.responseText,
      contentType = xhr.getResponseHeader('Content-Type');

    if (xhr.status == 0) {
      msg = gettext('Connection to the server has been lost.');
      promptmsg = gettext('Connection Lost');
    } else {
      if (contentType) {
        try {
          if (contentType.indexOf('application/json') == 0) {
            var resp = JSON.parse(msg);

            if (resp.result != null && (!resp.errormsg || resp.errormsg == '') &&
              onJSONResult && typeof(onJSONResult) == 'function') {
              return onJSONResult(resp.result);
            }
            msg = _.escape(resp.result) || _.escape(resp.errormsg) || 'Unknown error';
          }
          if (contentType.indexOf('text/html') == 0) {
            var alertMessage = promptmsg;
            if (type === 'error') {
              alertMessage = '\
                  <div class="media font-red-3 text-14">\
                    <div class="media-body media-middle">\
                      <div class="alert-text">' + promptmsg + '</div><br/>\
                      <div class="alert-text">' + gettext('Click for details.') + '</div>\
                    </div>\
                  </div>';
            }

            alertify.notify(
              alertMessage, type, 0,
              function() {
                alertify.pgIframeDialog().show().set({
                  frameless: false,
                }).set(
                  'pg_msg', msg
                );
              });
            return;
          }
        } catch (e) {
          alertify.alert().show().set('message', e.message).set(
            'title', 'Error'
          ).set('closable', true);
        }
      }
    }
    alertify.alert().show().set(
      'message', msg.replace(new RegExp(/\r?\n/, 'g'), '<br />')
    ).set('title', promptmsg).set('closable', true);
  };

  alertify.pgRespErrorNotify = (xhr, error, prefixMsg='') => {
    var contentType = xhr.getResponseHeader('Content-Type');
    try {
      if (xhr.status === 0) {
        error = gettext('Connection to the server has been lost.');
      } else {
        if(contentType){
          if(contentType.indexOf('application/json') >= 0) {
            var resp = JSON.parse(xhr.responseText);
            error = _.escape(resp.result) || _.escape(resp.errormsg) || gettext('Unknown error');
          }
        }
        if (contentType.indexOf('text/html') >= 0) {
          var alertMessage = '\
                <div class="media font-red-3 text-14">\
                  <div class="media-body media-middle">\
                    <div class="alert-text">' + gettext('INTERNAL SERVER ERROR') + '</div><br/>\
                    <div class="alert-text">' + gettext('Click for details.') + '</div>\
                  </div>\
                </div>';

          alertify.notify(
            alertMessage, 'error', 0, () => {
              alertify.pgIframeDialog()
                .show()
                .set({frameless: false})
                .set('pg_msg', xhr.responseText);
            }
          );
          return;
        }
      }
    }
    catch(e){
      error = e.message;
    }
    alertify.error(prefixMsg +' '+error);
  };

  var alertifyDialogResized = function(stop) {
    var self = this;

    if (stop) {
      self.pgResizeRecursion = false;
    }

    if (self.pgResizeTimeout) {
      return;
    }

    self.pgResizeTimeout = setTimeout(
      function() {
        var $el = $(this.elements.dialog),
          w = $el.width();

        this.pgResizeTimeout = null;

        if (w <= 480) {
          w = 'xs';
        } else if (w < 600) {
          w = 'sm';
        } else if (w < 768) {
          w = 'md';
        } else {
          w = 'lg';
        }

        $el.attr('el', w);
      }.bind(self),
      100
    );
  };

  var alertifyDialogStartResizing = function(start) {
    var self = this;

    if (start) {
      self.pgResizeRecursion = true;
    }

    setTimeout(
      function() {
        alertifyDialogResized.apply(self);

        if (self.pgResizeRecursion) {
          alertifyDialogStartResizing.apply(self, [false]);
        }
      }, 100
    );
  };

  alertify.pgDialogBuild = function() {
    this.set('onshow', function() {
      this.elements.dialog.classList.add('pg-el-container');
      $(this.elements.commands.close).attr('title', gettext('Close'));
      $(this.elements.commands.maximize).attr('title', gettext('Maximize'));
      alertifyDialogResized.apply(this, arguments);
    });
    this.set('onresize', alertifyDialogStartResizing.bind(this, true));
    this.set('onresized', alertifyDialogResized.bind(this, true));
    this.set('onmaximized', alertifyDialogResized);
    this.set('onrestored', alertifyDialogResized);
  };

  alertify.pgHandleItemError = function(xhr, error, message, args) {
    var pgBrowser = window.pgAdmin.Browser;

    if (!xhr || !pgBrowser) {
      return;
    }

    var contentType = xhr.getResponseHeader('Content-Type'),
      jsonResp = contentType &&
      contentType.indexOf('application/json') == 0 &&
      JSON.parse(xhr.responseText);

    if (
      jsonResp && (
        xhr.status == 503 ? (
          jsonResp.info == 'CONNECTION_LOST' &&
          'server' in args.info && jsonResp.data.sid >= 0 &&
          jsonResp.data.sid == args.info.server._id
        ) : (
          xhr.status == 428 &&
          jsonResp.errormsg &&
          jsonResp.errormsg == gettext('Connection to the server has been lost.')
        )
      )
    ) {
      if (
        args.preHandleConnectionLost &&
        typeof(args.preHandleConnectionLost) == 'function'
      ) {
        args.preHandleConnectionLost.apply(this, arguments);
      }

      // Check the status of the maintenance server connection.
      var server = pgBrowser.Nodes['server'],
        ctx = {
          resp: jsonResp,
          xhr: xhr,
          args: args,
        },
        reconnectServer = function() {
          var ctx = this,
            onServerConnect = function(_sid, _i, _d) {
              // Yay - server is reconnected.
              if (this.args.info.server._id == _sid) {
                pgBrowser.Events.off(
                  'pgadmin:server:connected', onServerConnect
                );
                pgBrowser.Events.off(
                  'pgadmin:server:connect:cancelled', onConnectCancel
                );

                // Do we need to connect the disconnected server now?
                if (
                  this.resp.data.database &&
                  this.resp.data.database != _d.db
                ) {
                  // Server is connected now, we will need to inform the
                  // database to connect it now.
                  pgBrowser.Events.trigger(
                    'pgadmin:database:connection:lost', this.args.item,
                    this.resp, true
                  );
                }
              }
            }.bind(ctx),
            onConnectCancel = function(_sid, _item, _data) {
              // User has cancelled the operation in between.
              if (_sid == this.args.info.server.id) {
                pgBrowser.Events.off('pgadmin:server:connected', onServerConnect);
                pgBrowser.Events.off('pgadmin:server:connect:cancelled', onConnectCancel);

                // Connection to the database will also be cancelled
                pgBrowser.Events.trigger(
                  'pgadmin:database:connect:cancelled', _sid,
                  this.resp.data.database || _data.db, _item, _data
                );
              }
            }.bind(ctx);

          pgBrowser.Events.on('pgadmin:server:connected', onServerConnect);
          pgBrowser.Events.on('pgadmin:server:connect:cancelled', onConnectCancel);

          // Connection to the server has been lost, we need to inform the
          // server first to take the action first.
          pgBrowser.Events.trigger(
            'pgadmin:server:connection:lost', this.args.item, this.resp
          );
        }.bind(ctx);

      $.ajax({
        url: server.generate_url(
          null, 'connect', args.info.server, true, args.info
        ),
        dataType: 'json',
        success: function(res) {
          if (res.success && 'connected' in res.data) {
            if (res.data.connected) {
              // Server is connected, but - the connection with the
              // particular database has been lost.
              pgBrowser.Events.trigger(
                'pgadmin:database:connection:lost', args.item, jsonResp
              );
              return;
            }
          }

          // Serever was not connected, we should first try to connect
          // the server.
          reconnectServer();
        },
        error: function() {
          reconnectServer();
        },
      });
      return true;
    }
    return false;
  };

  var alertifySuccess = alertify.success,
    alertifyError = alertify.error;

  /*
  For adding the jasmine test cases, we needed to refer the original success,
   and error functions, as orig_success and orig_error respectively.
  */
  _.extend(alertify, {
    orig_success: alertifySuccess,
    orig_error: alertifyError,
  });

  _.extend(alertify, {
    success: function(message, timeout, callback) {
      var alertMessage = '\
      <div class="media font-green-3 text-14">\
        <div class="media-body media-middle">\
          <div class="alert-icon success-icon">\
            <i class="fa fa-check" aria-hidden="true"></i>\
          </div>\
            <div class="alert-text">' + message + '</div>\
        </div>\
      </div>';
      return alertify.orig_success(alertMessage, timeout, callback);
    },
    error: function(message, timeout, callback) {
      var alertMessage = '\
      <div class="media font-red-3 text-14">\
        <div class="media-body media-middle">\
          <div class="alert-icon error-icon">\
            <i class="fa fa-exclamation-triangle" aria-hidden="true"></i>\
          </div>\
            <div class="alert-text">' + message + '</div>\
        </div>\
      </div>';
      return alertify.orig_error(alertMessage, timeout, callback);
    },
    info: function(message, timeout) {
      var alertMessage = '\
      <div class="media alert-info font-blue text-14">\
        <div class="media-body media-middle">\
          <div class="alert-icon info-icon">\
            <i class="fa fa-info" aria-hidden="true"></i>\
          </div>\
            <div class="alert-text">' + message + '</div>\
        </div>\
      </div>';
      var alert = alertify.notify(alertMessage, timeout);
      return alert;
    },
  });

  // Confirm dialogue: Set title attribute
  alertify.confirm().set({onshow:function() {
    $(this.elements.commands.close).attr('title', gettext('Close'));
    $(this.elements.commands.maximize).attr('title', gettext('Maximize'));
  }});

  return alertify;
});
