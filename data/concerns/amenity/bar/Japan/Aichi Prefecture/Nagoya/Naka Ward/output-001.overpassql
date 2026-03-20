[out:json][timeout:30];
area["name:en"="Nagoya"]->.outer;
area["name:en"="Naka Ward"]->.inner;
(
  nwr["amenity"="bar"](area.inner)(area.outer);
);
out geom;
