[out:json][timeout:30];
area["name:en"="Osaka"]->.outer;
area["name:en"="Osaka Prefecture"]->.inner;
(
  nwr["amenity"~"casino"](area.inner)(area.outer);
);
out geom;
