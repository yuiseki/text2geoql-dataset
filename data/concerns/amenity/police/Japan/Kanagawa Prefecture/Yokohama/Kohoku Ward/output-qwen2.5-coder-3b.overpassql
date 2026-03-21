[out:json][timeout:30];
area["name:en"="Kohoku Ward"]->.outer;
area["name:en"="Yokohama"]->.inner;
(
  nwr["amenity"~"police"](area.inner)(area.outer);
);
out geom;
