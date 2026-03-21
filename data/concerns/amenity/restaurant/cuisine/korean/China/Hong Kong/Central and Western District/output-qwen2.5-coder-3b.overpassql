[out:json][timeout:30];
area["name:en"="Central and Western District"]->.outer;
area["name:zh"="中西區"]->.inner;
(
  nwr["amenity"~"restaurant"]["cuisine"~"korean"](area.inner)(area.outer);
);
out geom;
