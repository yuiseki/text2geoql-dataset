[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
area["name:en"="Seocho-gu"]->.inner;
(
  nwr["amenity"="restaurant"]["cuisine"~"thai"](area.inner)(area.outer);
);
out geom;
