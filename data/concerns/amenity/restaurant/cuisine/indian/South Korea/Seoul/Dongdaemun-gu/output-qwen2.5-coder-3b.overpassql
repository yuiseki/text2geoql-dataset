[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
area["name:en"="Dongdaemun-gu"]->.inner;
(
  nwr["amenity"="restaurant"]["cuisine"~"indian"](area.inner)(area.outer);
);
out geom;
