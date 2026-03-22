[out:json][timeout:30];
area["name:en"="Ho Chi Minh City"]->.outer;
area["name:en"="Ho Chi Minh City"]->.inner;
(
  nwr["amenity"="cafe"](area.inner)(area.outer);
);
out geom;