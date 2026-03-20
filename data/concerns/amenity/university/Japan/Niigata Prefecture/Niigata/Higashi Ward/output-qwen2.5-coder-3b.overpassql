[out:json][timeout:30];
area["name:ja"="新潟県"]->.outer;
area["name:en"="Niigata"]->.inner;
(
  nwr["amenity"="university"](area.inner)(area.outer);
);
out geom;
