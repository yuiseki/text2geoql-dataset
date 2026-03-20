[out:json][timeout:30];
area["name:en"="Japan"]->.outer;
area["name:ja"="新潟県"]->.inner;
(
  nwr["tourism"="caravan_site"](area.inner)(area.outer);
);
out geom;
