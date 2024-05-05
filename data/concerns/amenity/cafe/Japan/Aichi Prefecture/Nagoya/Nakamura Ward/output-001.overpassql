[out:json][timeout:30000];
area["name:en"="Nakamura Ward"]->.outer;
area["name:en"="Nagoya"]->.inner;
(
  nwr["amenity"="cafe"](area.inner)(area.outer);
);
out geom;
