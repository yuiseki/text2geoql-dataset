[out:json][timeout:30];
area["name:ja"="福岡市"]->.outer;
area["name:ja"="福岡県"]->.inner;
(
  nwr["amenity"="restaurant"]["cuisine"~"italian"](area.inner)(area.outer);
);
out geom;
