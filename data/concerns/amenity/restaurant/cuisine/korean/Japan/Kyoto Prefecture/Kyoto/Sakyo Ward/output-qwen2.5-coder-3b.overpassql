[out:json][timeout:30];
area["name:en"="Kyoto"]->.outer;
area["name:en"="Kyoto Prefecture"]->.inner;
(
  nwr["amenity"~"restaurant"]["cuisine"~"korean"](area.inner)(area.outer);
);
out geom;
