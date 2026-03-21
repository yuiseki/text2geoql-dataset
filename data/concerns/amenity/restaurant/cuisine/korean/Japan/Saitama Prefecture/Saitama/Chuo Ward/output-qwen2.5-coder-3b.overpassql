[out:json][timeout:30];
area["name:en"="Saitama"]->.outer;
area["name:en"="Saitama Prefecture"]->.inner;
(
  nwr["amenity"~"restaurant"]["cuisine"~"korean"](area.inner)(area.outer);
);
out geom;
