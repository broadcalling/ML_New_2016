define(["backbone"], function(Backbone) {
  /**
   * Simple model for an asset.
   */
  var Asset = Backbone.Model.extend({
    defaults: {
      display_name: "",
      thumbnail: "",
      date_added: "",
      url: "",
      external_url: "",
      portable_url: "",
      locked: false
    },
    _infer_asset_type: function(){
      var name_segments = this.get("display_name").split(".");
      var seg_len = name_segments.length;
      var asset_type = (seg_len > 1) ? name_segments[seg_len - 1].toUpperCase() : "";
      this.set("asset_type", asset_type);
    },
    initialize: function(){
      this._infer_asset_type();
      Backbone.Model.prototype.initialize.call(this);
    },
    events: {
        'change:display_name': '_infer_asset_type'
    }
  });
  return Asset;
});
