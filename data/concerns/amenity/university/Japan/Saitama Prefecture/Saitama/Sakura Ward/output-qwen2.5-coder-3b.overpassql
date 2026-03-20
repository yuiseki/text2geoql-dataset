[out:json][timeout:30];
area["name:ja"="桜区"]->.outer;
area["name:en"="Sakura Ward"]->.inner;
(
  nwr["amenity"="university"](area.inner)(area.outer);
);
out geom;
