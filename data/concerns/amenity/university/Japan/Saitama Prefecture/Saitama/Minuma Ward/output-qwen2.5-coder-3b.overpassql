[out:json][timeout:30];
area["name:ja"="さいたま市"]->.outer;
area["name:en"="Saitama"]->.inner;
(
  nwr["amenity"="university"](area.inner)(area.outer);
);
out geom;
