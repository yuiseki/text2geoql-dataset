[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
area["name:en"="Dongjak-gu"]->.inner;
(
  nwr["amenity"="dentist"](area.inner)(area.outer);
);
out geom;
