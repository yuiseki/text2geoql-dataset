// Important note: SubArea: Kosovo/Municipality of Pristina
[out:json][timeout:30000];
area["name:en"="Municipality of Pristina"]->.searchArea;
(
  relation["boundary"="administrative"]["admin_level"=8](area.searchArea);
);
out meta;
