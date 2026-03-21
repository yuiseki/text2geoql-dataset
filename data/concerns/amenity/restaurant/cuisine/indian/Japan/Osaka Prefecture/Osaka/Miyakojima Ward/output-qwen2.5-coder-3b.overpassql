[out:json][timeout:30];
area["name:en"="Osaka"]->.outer;
area["name:en"="Osaka Prefecture"]->.inner;
(
  nwr["amenity"="restaurant"]["cuisine"~"indian"](area.inner)(area.outer);
);
out geom;
