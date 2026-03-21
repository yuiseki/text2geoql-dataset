[out:json][timeout:30];
area["name:en"="Hong Kong"]->.outer;
area["name:zh"~"香港"]->.inner;
(
  nwr["amenity"="restaurant"]["cuisine"~"korean"](area.inner)(area.outer);
);
out geom;
