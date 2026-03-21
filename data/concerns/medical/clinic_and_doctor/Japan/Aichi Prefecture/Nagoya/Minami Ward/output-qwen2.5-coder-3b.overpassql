[out:json][timeout:30];
area["name:en"="Minami Ward"]->.outer;
area["name:en"="Nagoya"]->.inner;
(
  nwr["amenity"~"clinic|doctor"](area.inner)(area.outer);
);
out geom;
