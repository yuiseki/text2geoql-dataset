[out:json][timeout:30];
area["name:ja"="長野県"]->.outer;
area["name:ja"="長野市"]->.inner;
(
  nwr["tourism"="alpine_hut"](area.inner)(area.outer);
);
out geom;
