[out:json][timeout:30];
area["name:en"="Andalusia"]->.outer;
area["name:en"="Seville"]->.inner;
(
  nwr["amenity"="restaurant"](area.inner)(area.outer);
);
out geom;