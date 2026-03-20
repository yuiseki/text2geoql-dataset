[out:json][timeout:30];
area["name:en"="Nagoya"]->.outer;
area["name:en"="Minato Ward"]->.inner;
(
  nwr["amenity"="hospital"](area.inner)(area.outer);
);
out geom;
