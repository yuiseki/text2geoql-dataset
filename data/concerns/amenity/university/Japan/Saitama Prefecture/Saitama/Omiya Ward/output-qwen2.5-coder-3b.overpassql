[out:json][timeout:30];
area["name:ja"="新宿区"]->.outer;
area["name:en"="Shinjuku"]->.inner;
(
  nwr["amenity"="university"](area.inner)(area.outer);
);
out geom;
