[out:json][timeout:30];
area["name:en"="Saitama"]->.outer;
area["name:en"="Saitama Prefecture"]->.inner;
(
  nwr["tourism"="camp_site"](area.inner)(area.outer);
);
out geom;
