<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.38.0-Grenoble" styleCategories="Symbology">
  <pipe-data-defined-properties>
    <Option type="Map">
      <Option name="name" value="" type="QString"/>
      <Option name="properties"/>
      <Option name="type" value="collection" type="QString"/>
    </Option>
  </pipe-data-defined-properties>
  <pipe>
    <provider>
      <resampling zoomedInResamplingMethod="nearestNeighbour" maxOversampling="2" zoomedOutResamplingMethod="nearestNeighbour" enabled="false"/>
    </provider>
    <rasterrenderer classificationMax="335" band="3" alphaBand="-1" opacity="1" classificationMin="0" nodataColor="122,4,3,0,rgb:0.47843137254901963,0.01568627450980392,0.01176470588235294,0" type="singlebandpseudocolor">
      <rasterTransparency/>
      <minMaxOrigin>
        <limits>None</limits>
        <extent>WholeRaster</extent>
        <statAccuracy>Estimated</statAccuracy>
        <cumulativeCutLower>0.02</cumulativeCutLower>
        <cumulativeCutUpper>0.98</cumulativeCutUpper>
        <stdDevFactor>2</stdDevFactor>
      </minMaxOrigin>
      <rastershader>
        <colorrampshader clip="0" colorRampType="DISCRETE" maximumValue="335" labelPrecision="0" classificationMode="2" minimumValue="0">
          <colorramp name="[source]" type="gradient">
            <Option type="Map">
              <Option name="color1" value="122,4,3,255,rgb:0.47843137254901963,0.01568627450980392,0.01176470588235294,1" type="QString"/>
              <Option name="color2" value="122,4,3,255,rgb:0.47843137254901963,0.01568627450980392,0.01176470588235294,1" type="QString"/>
              <Option name="direction" value="ccw" type="QString"/>
              <Option name="discrete" value="0" type="QString"/>
              <Option name="rampType" value="gradient" type="QString"/>
              <Option name="spec" value="rgb" type="QString"/>
              <Option name="stops" value="0.00298507;255,0,255,255,rgb:1,0,1,1;rgb;ccw:0.0925373;89,236,255,255,rgb:0.34901960784313724,0.92549019607843142,1,1;rgb;ccw:0.176119;56,167,218,255,rgb:0.2196078431372549,0.65490196078431373,0.85490196078431369,1;rgb;ccw:0.268657;101,144,45,255,rgb:0.396078431372549,0.56470588235294117,0.17647058823529413,1;rgb;ccw:0.358209;162,221,68,255,rgb:0.63529411764705879,0.8666666666666667,0.26666666666666666,1;rgb;ccw:0.450746;222,238,49,255,rgb:0.87058823529411766,0.93333333333333335,0.19215686274509805,1;rgb;ccw:0.495522;252,115,3,255,rgb:0.9882352941176471,0.45098039215686275,0.01176470588235294,1;rgb;ccw:0.632836;234,0,39,255,rgb:0.91764705882352937,0,0.15294117647058825,1;rgb;ccw:1.08657;206,5,5,255,hsv:0,0.97647058823529409,0.80784313725490198,1;rgb;ccw" type="QString"/>
            </Option>
          </colorramp>
          <item value="0" color="#7a0403" label="Continuous" alpha="255"/>
          <item value="1" color="#ff00ff" label="No growing season" alpha="255"/>
          <item value="31" color="#59ecff" label="Jan" alpha="255"/>
          <item value="59" color="#38a7da" label="Feb" alpha="255"/>
          <item value="90" color="#65902d" label="Mar" alpha="255"/>
          <item value="120" color="#a2dd44" label="Apr" alpha="255"/>
          <item value="151" color="#deee31" label="May" alpha="255"/>
          <item value="166" color="#fc7303" label="Early Jun" alpha="255"/>
          <item value="212" color="#ea0027" label="Late Jun-Jul" alpha="255"/>
          <item value="364" color="#ce0505" label="Aug-Dec" alpha="255"/>
          <item value="365" color="#7a0403" label="Continuous" alpha="255"/>
          <rampLegendSettings maximumLabel="" prefix="" orientation="2" useContinuousLegend="1" direction="0" minimumLabel="" suffix="">
            <numericFormat id="basic">
              <Option type="Map">
                <Option name="decimal_separator" type="invalid"/>
                <Option name="decimals" value="6" type="int"/>
                <Option name="rounding_type" value="0" type="int"/>
                <Option name="show_plus" value="false" type="bool"/>
                <Option name="show_thousand_separator" value="true" type="bool"/>
                <Option name="show_trailing_zeros" value="false" type="bool"/>
                <Option name="thousand_separator" type="invalid"/>
              </Option>
            </numericFormat>
          </rampLegendSettings>
        </colorrampshader>
      </rastershader>
    </rasterrenderer>
    <brightnesscontrast gamma="1" contrast="0" brightness="0"/>
    <huesaturation invertColors="0" colorizeBlue="128" colorizeGreen="128" colorizeStrength="100" colorizeRed="255" grayscaleMode="0" colorizeOn="0" saturation="0"/>
    <rasterresampler maxOversampling="2"/>
    <resamplingStage>resamplingFilter</resamplingStage>
  </pipe>
  <blendMode>0</blendMode>
</qgis>
