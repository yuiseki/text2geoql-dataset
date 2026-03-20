[out:json][timeout:30];
area["name:en"="Japan"]->.outer;
area["name:ja"="静岡県"]->.inner;
(
  nwr["tourism"="caravan_site"](area.inner)(area.outer);
);
out geom;
