[out:json][timeout:30];
area["name:en"="Hong Kong"]->.outer;
(
  nwr["tourism"="camp_site"](area.outer);
);
out geom;
