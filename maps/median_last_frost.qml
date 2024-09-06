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
    <rasterrenderer classificationMax="335" band="2" alphaBand="-1" opacity="1" classificationMin="0" nodataColor="" type="singlebandpseudocolor">
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
        <colorrampshader clip="0" colorRampType="DISCRETE" maximumValue="335" labelPrecision="4" classificationMode="2" minimumValue="0">
          <colorramp name="[source]" type="gradient">
            <Option type="Map">
              <Option name="color1" value="122,4,3,255,rgb:0.47843137254901963,0.01568627450980392,0.01176470588235294,1" type="QString"/>
              <Option name="color2" value="234,211,236,255,rgb:0.91764705882352937,0.82745098039215681,0.92549019607843142,1" type="QString"/>
              <Option name="direction" value="ccw" type="QString"/>
              <Option name="discrete" value="0" type="QString"/>
              <Option name="rampType" value="gradient" type="QString"/>
              <Option name="spec" value="rgb" type="QString"/>
              <Option name="stops" value="0.540299;242,20,58,255,rgb:0.94901960784313721,0.07843137254901961,0.22745098039215686,1;rgb;ccw:0.632836;243,119,39,255,rgb:0.95294117647058818,0.46666666666666667,0.15294117647058825,1;rgb;ccw:0.725373;255,240,70,255,rgb:1,0.94117647058823528,0.27450980392156865,1;rgb;ccw:0.814925;140,233,53,255,rgb:0.5490196078431373,0.9137254901960784,0.20784313725490197,1;rgb;ccw:0.907463;27,211,70,255,rgb:0.10588235294117647,0.82745098039215681,0.27450980392156865,1;rgb;ccw:0.997015;53,192,194,255,rgb:0.20784313725490197,0.75294117647058822,0.76078431372549016,1;rgb;ccw:1.08657;180,241,247,255,rgb:0.70588235294117652,0.94509803921568625,0.96862745098039216,1;rgb;ccw" type="QString"/>
            </Option>
          </colorramp>
          <item value="0" color="#7a0403" label="Continous" alpha="255"/>
          <item value="181" color="#f2143a" label="Jun" alpha="255"/>
          <item value="212" color="#f37727" label="Jul" alpha="255"/>
          <item value="243" color="#fff046" label="Aug" alpha="255"/>
          <item value="273" color="#8ce935" label="Sep" alpha="255"/>
          <item value="304" color="#1bd346" label="Oct" alpha="255"/>
          <item value="334" color="#35c0c2" label="Nov" alpha="255"/>
          <item value="364" color="#b4f1f7" label="Dec" alpha="255"/>
          <item value="365" color="#ead3ec" label="No growing season" alpha="255"/>
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
