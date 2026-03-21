[out:json][timeout:30];
area["name:ja"="長崎県"]->.outer;
area["name:ja"="長崎市"]->.inner;
(
  nwr["amenity"~"social_facility"](area.inner)(area.outer);
);
out geom;
