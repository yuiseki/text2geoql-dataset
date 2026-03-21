[out:json][timeout:30];
area["name:en"="Minami Ward"]->.outer;
area["name:en"="Fukuoka"]->.inner;
(
  nwr["amenity"~"clinic|doctor"](area.inner)(area.outer);
);
out geom;
